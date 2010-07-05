#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include "runner.h"

void stdoutWritten(char*);

struct Runner {
	void *writeStdout;
};

int main(int argc, char* argv[])
{
	// Tries to compare 2 packages version.
	if (argc < 3)
	{
		printf("Please provide 2 packages.\n");
		return -1;
	}

	char *str = malloc((strlen(argv[1]) + strlen(argv[2]) + 2) * sizeof(char));

	sprintf(str, "%s %s", argv[1], argv[2]);

	Runner *r = createRunner();
	r->writeStdout = stdoutWritten;
	int ret = execute(r, str);
	if (ret < 0)
		printf("Execution error\n");
	
	freeRunner(r);

	return 0;
}

void stdoutWritten(char *data)
{
	printf("From program : %s\n", data);
}

Runner *createRunner()
{
	Runner *ret = malloc(sizeof(Runner));
	return ret;
}

int execute(Runner *r, char *args)
{
	r = r;
	int ret = fork();
	if (ret > 0)
	{
		printf("New PID = %d\n", ret);
		return ret;
	}
	
	//printf("args = %s\n", args);
	//int fd = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);

	int fd = socket(AF_INET, SOCK_STREAM, 0);
	if (fd < 0) 
		printf("ERROR opening socket\n");
	
	struct sockaddr_in serv_addr;

	memset(&serv_addr, 0, sizeof(serv_addr));
	int portno = 5555;
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = INADDR_ANY;
	serv_addr.sin_port = htons(portno);
	if (connect(fd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) 
		printf("ERROR on connecting\n");
	
	//listen(fd, 5);

	dup2(fd, STDOUT_FILENO);
	ret = execl("/home/detlev/src/c-portage/src/test.py", "test.py", "app-portage/kuroo4-4.2", "app-portage/kuroo4-4.3", NULL);
	printf("execl: (%d) %s\n", errno, strerror(errno));
	return ret;
}

void freeRunner(Runner *r)
{
	free(r);
}
