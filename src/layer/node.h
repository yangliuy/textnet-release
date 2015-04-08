#ifndef TEXTNET_LAYER_NODE_H_
#define TEXTNET_LAYER_NODE_H_

#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <mshadow/tensor.h>
#include <mshadow/tensor_container.h>
#include "../utils/utils.h"
#include "../utils/io.h"
#include "../initializer/initializer.h"
#include "../updater/updater.h"

/*! \brief namespace of textnet */
namespace textnet {
/*! \brief namespace of layer defintiion */
namespace layer {
template<typename xpu>
struct Node {
  mshadow::TensorContainer<xpu, 4> data;
  mshadow::TensorContainer<xpu, 4> diff;
  mshadow::TensorContainer<xpu, 1> idx;
  mshadow::TensorContainer<xpu, 1> length;
  bool must_contiguous;
  bool inited_data;
  bool inited_diff;
  bool is_share;
  std::string node_name;
  int node_idx;
  bool need_diff;
  updater::Updater<xpu, 4>* updater_;
  initializer::Initializer<xpu, 4>* initializer_;

  // orc
  void ClearDiff(void) {
    if (!is_share) {
      diff = 0.f;
      if (updater_ && updater_->is_sparse) {
        diff.Resize(mshadow::Shape4(0, 0, 0, 0), 0);
        idx.Resize(mshadow::Shape1(0), 0);
      }
    }
  };

  // orc
  void Share(const Node &other) {
    is_share = true;
    data = other.data;
    diff = other.diff;
    idx  = other.idx;
    length  = other.length;
    must_contiguous = other.must_contiguous;
    inited_diff = false; // main node take charge of this
    inited_diff = false; // main node take charge of this
    node_name = other.node_name;
    node_idx = other.node_idx;
    need_diff = other.need_diff;
    
    updater_ = NULL;     // main node take charge of this
    initializer_ = NULL; // main node take charge of this 
  }
  
  // constructor
  Node(bool need_diff_ = true) : must_contiguous(false), need_diff(need_diff_) {
    data.shape_ = mshadow::Shape4(0,0,0,0);
    diff.shape_ = mshadow::Shape4(0,0,0,0);
    length.shape_ = mshadow::Shape1(0);
    idx.shape_ = mshadow::Shape1(0);
    // data.set_pad(false);
    // diff.set_pad(false);
    inited_data = false;
    inited_diff = false;
    is_share = false;
    updater_ = NULL;
    initializer_ = NULL;
  }
  
  inline void FreeSpace(void) {
    if (inited_data){
      mshadow::FreeSpace(&data);
      mshadow::FreeSpace(&length);
    }
    if (inited_diff){
      mshadow::FreeSpace(&diff);
    }
  }

  inline void PrintShape(std::string text) {
	mshadow::Shape<4> s = data.shape_;
	// utils::Printf("\t%s Shape: %d x %d x %d x %d\n", text.c_str(), s[0], s[1], s[2], s[3]);
  }

  inline void Resize(int d1, int d2, int d3, int d4, bool init=false) {
    mshadow::Shape<4> new_size = mshadow::Shape4(d1, d2, d3, d4);
    if (4 == data.shape_.kDimension && new_size == data.shape_ && !init) {
      // do nothing
    } else if (init) {
      data.Resize(new_size, 0.0);
      length.Resize(mshadow::Shape1(d1), 0.0);
      inited_data = true;
      if (need_diff) {
        diff.Resize(new_size, 0.0);
        inited_diff = true;
      }
    } else {
      data.Resize(new_size);
      length.Resize(mshadow::Shape1(d1));
      inited_data = true;
      if (need_diff) {
        diff.Resize(new_size);
        inited_diff = true;
      }
    }
  }
  
  inline void Resize(mshadow::Shape<4> new_size, bool init=false) {
    if (4 == data.shape_.kDimension && new_size == data.shape_ && !init) {
      // do nothing
    } else if (init) {
      data.Resize(new_size, 0.0);
      length.Resize(mshadow::Shape1(new_size[0]), 0.0);
      inited_data = true;
      if (need_diff) {
        diff.Resize(new_size, 0.0);
        inited_diff = true;
      }
    } else {
      data.Resize(new_size);
      length.Resize(mshadow::Shape1(new_size[0]));
      inited_data = true;
      if (need_diff) {
        diff.Resize(new_size);
        inited_diff = true;
      }
    }
  }
  
  inline mshadow::Tensor<xpu, 1> data_d1() {
    return mshadow::Tensor<xpu, 1>(data.dptr_, mshadow::Shape1(data.shape_.Size()));
  }

  inline mshadow::Tensor<xpu, 1> diff_d1() {
    return mshadow::Tensor<xpu, 1>(diff.dptr_, mshadow::Shape1(diff.shape_.Size()));
  }

  inline mshadow::Tensor<xpu, 1> idx_d1() {
    return mshadow::Tensor<xpu, 1>(idx.dptr_, mshadow::Shape1(idx.shape_.Size()));
  }
  
  inline mshadow::Tensor<xpu, 2> data_d2() {
    mshadow::Shape<4> s = data.shape_;
    index_t  ymax = s[1]*s[2]*s[3];
    return mshadow::Tensor<xpu, 2>(data.dptr_, mshadow::Shape2(s[0], ymax));
  }

  inline mshadow::Tensor<xpu, 2> data_d2_reverse() {
    mshadow::Shape<4> s = data.shape_;
    index_t  xmax = s[0]*s[1]*s[2];
    return mshadow::Tensor<xpu, 2>(data.dptr_, mshadow::Shape2(xmax, s[3]));
  }

  inline mshadow::Tensor<xpu, 2> diff_d2() {
    mshadow::Shape<4> s = diff.shape_;
    index_t  ymax = s[1]*s[2]*s[3];
    return mshadow::Tensor<xpu, 2>(diff.dptr_, mshadow::Shape2(s[0], ymax));
  }
  inline mshadow::Tensor<xpu, 2> diff_d2_reverse() {
    mshadow::Shape<4> s = diff.shape_;
    index_t  xmax = s[0]*s[1]*s[2];
    return mshadow::Tensor<xpu, 2>(diff.dptr_, mshadow::Shape2(xmax, s[3]));
  }
 
  inline mshadow::Tensor<xpu, 3> data_d3() {
    mshadow::Shape<4> s = data.shape_;
    index_t  ymax = s[2]*s[3];
    return mshadow::Tensor<xpu, 3>(data.dptr_, mshadow::Shape3(s[0], s[1], ymax));
  }

  inline mshadow::Tensor<xpu, 3> diff_d3() {
    mshadow::Shape<4> s = diff.shape_;
    index_t  ymax = s[2]*s[3];
    return mshadow::Tensor<xpu, 3>(diff.dptr_, mshadow::Shape3(s[0], s[1], ymax));
  }
  
  inline void Init(bool init_diff = false) { // why init diff?
    if (!is_share) {
      initializer_->DoInitialize(data);
      if (init_diff) {
        initializer_->DoInitialize(diff);
      }
    }
  }
  
  inline void Update() {
    if (!is_share) {
      if (updater_->is_sparse) {
        updater_->UpdateSparse(data, diff, idx);
      } else {
        updater_->Update(data, diff);
      }
    }
  }
  void sparseAdd(mshadow::TensorContainer<xpu, 4> &l_data, 
                 mshadow::TensorContainer<xpu, 1> &l_idx, 
                 mshadow::TensorContainer<xpu, 4> &r_data, 
                 mshadow::TensorContainer<xpu, 1> &r_idx,
                 mshadow::TensorContainer<xpu, 4> &merge_data,
                 mshadow::TensorContainer<xpu, 1> &merge_idx) {
    utils::Assert(l_data.size(2) == 1 && r_data.size(2) == 1, "Merge Sparse Tensor: size problem");
    utils::Assert(l_data.size(3) == 1 && r_data.size(3) == 1, "Merge Sparse Tensor: size problem");
    utils::Assert(l_data.size(1) == r_data.size(1), "Merge Sparse Tensor: size problem");

    std::map<int, int> idx_map;
    int inc = 0;
    for (int i = 0; i < l_idx.size(0); ++i) {
      int w_idx = l_idx[i];
      if (!idx_map.count(w_idx)) {
        idx_map[w_idx] = inc++;
      }
    }
    for (int i = 0; i < r_idx.size(0); ++i) {
      int w_idx = r_idx[i];
      if (!idx_map.count(w_idx)) {
        idx_map[w_idx] = inc++;
      }
    }

    int feat_size = l_data.size(1);
    merge_data.Resize(mshadow::Shape4(inc, feat_size, 1, 1), 0);
    merge_idx.Resize(mshadow::Shape1(inc), 0);
    for (std::map<int,int>::iterator it=idx_map.begin(); it!=idx_map.end(); ++it) {
      merge_idx[it->second] = it->first;
    }
    for (int i = 0; i < l_data.size(0); ++i) {
      merge_data[idx_map[l_idx[i]]] += l_data[i];
    }
    for (int i = 0; i < r_data.size(0); ++i) {
      merge_data[idx_map[r_idx[i]]] += r_data[i];
    }
  }

  void sparseAdd2Left(mshadow::TensorContainer<xpu, 4> &l_data, 
                      mshadow::TensorContainer<xpu, 1> &l_idx, 
                      mshadow::TensorContainer<xpu, 4> &r_data, 
                      mshadow::TensorContainer<xpu, 1> &r_idx) {
    mshadow::TensorContainer<xpu, 4> merge_data;
    mshadow::TensorContainer<xpu, 1> merge_idx;
    sparseAdd(l_data, l_idx, r_data, r_idx, merge_data, merge_idx);
    l_data = merge_data;
    l_idx  = merge_idx;
  }

}; // struct Node

}  // namespace layer
}  // namespace textnet
#endif  // CXXNET_LAYER_NODE_H
