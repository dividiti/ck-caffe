#ifdef __MINGW32__
# include <sys/time.h>
#else
# ifdef WINDOWS
#  include <time.h>
# else
#  include <sys/time.h>
# endif
#endif  

double dk_dnn_proxy__get_time() {
#ifdef WINDOWS
  return clock() / double(CLOCKS_PER_SEC);
#else
  #ifdef __INTEL_COMPILERX
    return _rdtsc() / double(getCPUFreq());
  #else
    timeval t;
    gettimeofday(&t, 0);
    return t.tv_sec + t.tv_usec / 1e6;
  #endif
#endif 
}
