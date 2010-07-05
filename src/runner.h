
typedef struct Runner Runner;

Runner *createRunner();
int execute(Runner*, char*);
void freeRunner(Runner*);
