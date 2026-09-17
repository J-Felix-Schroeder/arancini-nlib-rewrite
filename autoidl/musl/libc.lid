library "/lib/aarch64-linux-gnu/libc.so.6";
u64 strlen(ptr s);
void qsort(ptr base, u64 n, u64 size, fnptr compare);
i32 printf(ptr format, ...);
i32 fflush(ptr stream);
i32 puts(ptr s);
i32 putchar(i32 c);
