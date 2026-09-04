#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
    long n = atol(argv[1]);
    long repeat = atol(argv[2]);
    char *string = malloc(n + 1);
    unsigned long total = 0;
    long i;

    memset(string, 'a', n);
    string[n] = 0;
    for (i = 0; i < repeat; i++) {
        string[0] = 'a' + (i & 1);
        total += strlen(string);
    }
    printf("strlen of %ld bytes %ld times = %lu\n", n, repeat, total);
    return 0;
}
