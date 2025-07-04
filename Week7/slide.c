#include <stdio.h>
int main() {
    char arr1[2];
    char c;
    char arr2[3];
    
    arr1[0] = 2;
    arr2[0] = 3; // This line is incorrect, it should be arr2[0] = 3;
    c = 7;
    printf("%d", arr2[0]); 
    return 0;
}
