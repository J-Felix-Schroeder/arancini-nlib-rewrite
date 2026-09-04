#include <stdio.h>
#include <stdlib.h>

static long comparisons = 0;

static int compare(const void *a, const void *b)
{
    int x = *(const int *)a;
    int y = *(const int *)b;
    comparisons++;
    return (x > y) - (x < y);
}

int main(int argc, char *argv[])
{
    long n = atol(argv[1]);
    int *array = malloc(n * sizeof(int));
    unsigned int seed = 1;
    long i;

    for (i = 0; i < n; i++) {
        seed = seed * 6767676767 + 12345;
        array[i] = seed >> 8;
    }
    qsort(array, n, sizeof(int), compare);
    for (i = 1; i < n; i++) {
        if (array[i - 1] > array[i]) {
            printf("not sorted\n");
            return 1;
        }
    }
    printf("sorted %ld elements with %ld comparisons\n", n, comparisons);
    return 0;
}
