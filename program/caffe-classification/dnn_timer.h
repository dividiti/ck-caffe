#ifndef __DNN_TIMER_H_
#define __DNN_TIMER_H_

#ifdef __MINGW32__
# include <sys/time.h>
#else
# ifdef WINDOWS
#  include <time.h>
# else
#  include <sys/time.h>
# endif
#endif  

double dnn_get_time() {
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

#endif // __DNN_TIMER_H_
