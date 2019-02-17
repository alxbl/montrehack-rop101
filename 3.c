#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <malloc.h>
#include <sys/mman.h>

#define SIZE 0x100
#define PAGESZ 0x1000
#define MOTD_COUNT 3
const char default_motd[] = "<no message of the day set>\n";

int done = 0;

typedef struct motd_
{
    char* motd;
    int64_t rating ;
} motd_t;

void inspector_gadget()
{
    // Totally legitimate gadgets :)
    __asm("xchg %rax, %rdi");
    __asm("ret");

    __asm("mov %rsi, %rdx");
    __asm("ret");

    __asm("mov -4(%rbp), %rdx");
    __asm("ret");

    void* ptr = (void *)memalign(0x1000, 0x1000);
}

void clean_stdin()
{
    while (1)
    {
        char c = getchar();
        if (c == '\n') break;
        if (c == EOF) exit(1);
    }
}

int getnum()
{
    int choice = ~0;
    scanf("%d", &choice);
    clean_stdin();
    return choice;
}

motd_t* get_motd(motd_t* motds)
{
    printf("=> Which message of the day? (1-%d)\n> ", MOTD_COUNT);
    int idx = getnum();

    if (idx > MOTD_COUNT)
    {
        printf("This is not a valid index!\n");
        return NULL;
    }
    return (motds + (idx-1));
}


void read_motd(motd_t* motds) {
    motd_t* motd = get_motd(motds);
    if (!motd) return;

    printf("=> Type in the new message of the day please:\n> ");
    char buf[SIZE] = {0};
    // [bill] james said gets was dangerous. I think he's overreacting, but I fixed it to make the
    //        auditor happy.
    fgets(buf, SIZE, stdin);
    memcpy(motd->motd, buf, SIZE);
}

void show_motd(motd_t* motds) {
    motd_t* motd = get_motd(motds);
    if (!motd) return;
    printf("=> %s   Rated %d out of 10\n", motd->motd, motd->rating);
}

void rate_motd(motd_t* motds) {
    motd_t* motd = get_motd(motds);
    if (!motd) return;
    printf("=> %s Rating? (out of 10)\n> ", motd->motd);
    int rating = getnum();
    motd->rating = rating;
    printf("Thank you! Your opinion matters to us.\n");
}

void init(motd_t* motds)
{
    void* scratch = memalign(PAGESZ, PAGESZ); // Just to ensure that memalign is resolved. => avoid segv
    for (int i = 0; i < MOTD_COUNT; ++i)
    {
        motd_t* m = motds + i;
        m->rating = 0;
        m->motd = (char*)malloc(SIZE);
        memset(m->motd, 0, SIZE);
        memcpy(m->motd, default_motd, sizeof(default_motd));
        // [bill] james told me that last week's hacker executed the motd. This
        // should prevent him from doing it again.
        mprotect(m->motd, 1, PROT_READ | PROT_WRITE);
    }
}

void main()
{
    motd_t motds[MOTD_COUNT];
    init(motds);

    printf("motd daemon v0.3 (c) 2019 BetterSoft\n");
    printf("    Now with 100%% less system!\n");
    fflush(stdout);

    while (!done)
    {
        printf("\n");
        printf("=> How may I help you today?\n");
        printf("    1 - View message of the day\n");
        printf("    2 - Change message of the day\n");
        printf("    3 - Rate message of the day\n");
        printf("    4 - Exit\n");

        printf("> ");
        int choice = getnum();
        printf("\n");

        switch (choice)
        {
            case 1:
                show_motd(motds);
                break;
            case 2:
            {
                read_motd(motds);
                break;
            }
            case 3:
            {
                rate_motd(motds);
                break;
            }
            case 4:
                done = 1;
                break;
            default:
                printf("I don't recognize that option.\n");
                break;
        }
    }
    printf("Bye!\n");
}
