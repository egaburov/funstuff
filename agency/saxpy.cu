#include <cassert>
#include <iostream>
#include <chrono>
#include <agency/execution_policy.hpp>
#include <agency/cuda/execution_policy.hpp>
#include <thrust/device_vector.h>

struct Saxpy
{
  float a;
  const float *x, *y;
  float *z;
  __host__ __device__
  void operator()(agency::parallel_agent &self)
  {
    int i = self.index();
    z[i] = a * x[i] + y[i];
  }
};

void saxpy(size_t n, float a, const float* x, const float* y, float* z)
{
  using namespace agency;
  bulk_invoke(cuda::par(n), Saxpy{a,x,y,z});
}

int main()
{
  size_t n = 16 << 20;
  thrust::device_vector<float> x(n, 1), y(n, 2), z(n);
  float a = 13.;

  saxpy(n, a, raw_pointer_cast(x.data()), raw_pointer_cast(y.data()), raw_pointer_cast(z.data()));

  thrust::device_vector<float> ref(n, a * 1.f + 2.f);
  assert(ref == z);

  std::cout << "Measuring performance..." << std::endl;

  // time a number of trials
  size_t num_trials = 20;

  auto start = std::chrono::high_resolution_clock::now();
  for(size_t i = 0; i < num_trials; ++i)
  {
    saxpy(n, a, raw_pointer_cast(x.data()), raw_pointer_cast(y.data()), raw_pointer_cast(z.data()));
  }
  std::chrono::duration<double> elapsed = std::chrono::high_resolution_clock::now() - start;

  double seconds = elapsed.count() / num_trials;
  double gigabytes = double(3 * n * sizeof(float)) / (1 << 30);
  double bandwidth = gigabytes / seconds;

  std::cout << "SAXPY Bandwidth: " << bandwidth << " GB/s" << std::endl;

  return 0;
}
