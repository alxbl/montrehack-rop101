#include <stdlib.h>
#include <stdio.h>
#include <string.h>

char motd[SIZE] = "> > > D-d-d-DROP the ROP! < < <";

void clean_stdin()
{
    char c;
    while ((c = getchar()) != '\n');
}

int getnum()
{
    int choice;
    if (scanf("%d", &choice) == 1) return choice;
    clean_stdin();
    return ~0;
}

void read_motd(char* motd) {
    printf("Type in the new message of the day please:\n> ");
    char buf[SIZE] = {0};
    clean_stdin();
    gets(buf);
    memcpy(motd, buf, SIZE);
}

int done = 0;
void main()
{
    printf("motd daemon v0.1 (c) 2019 BetterSoft\n");
    fflush(stdout);
    system("date"); // [bill] This is easier than manipulating time and makes our code cleaner.

    while (!done)
    {
        printf("\n");
        printf("=> How may I help you today?\n");
        printf("    1 - View message of the day\n");
        printf("    2 - Change message of the day\n");
        printf("    3 - Exit\n");

        printf("> ");
        int choice = getnum();
        printf("\n");

        switch (choice)
        {
            case 1:
                puts(motd);
                break;
            case 2:
                read_motd(motd);
                break;
            case 3:
                done = 1;
                break;
            default:
                printf("I don't recognize that option.\n");
                break;
        }
    }
    printf("Bye!\n");
}
