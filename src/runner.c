/*
 * Compile command :
 * gcc -o runner -W -Wall -g --std=c99 runner.c
 */
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
	/*if (argc < 3)
	{
		printf("Please provide 2 packages.\n");
		return -1;
	}

	char *str = malloc((strlen(argv[1]) + strlen(argv[2]) + 2) * sizeof(char));

	sprintf(str, "%s %s", argv[1], argv[2]);
	*/
	Runner *r = createRunner();
	r->writeStdout = stdoutWritten;
	int ret = execute(r, "");
	
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
		// Listening socket
		int fd = socket(AF_INET, SOCK_STREAM, 0);
		if (fd < 0) 
			printf("ERROR opening socket\n");

		struct sockaddr_in serv_addr;

		memset(&serv_addr, 0, sizeof(serv_addr));
	
		int portno = 5555;
		serv_addr.sin_family = AF_INET;
		serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
		serv_addr.sin_port = htons(portno);
	
		if ((ret = bind(fd, (struct sockaddr *) &serv_addr, sizeof(serv_addr))) < 0) 
		{
			printf("ERROR on binding : %d, %d (%s)\n", ret, errno, strerror(errno));
			return ret;
		}
	
		if ((ret = listen(fd, 5)) < 0)
			printf("ERROR on listening : %d, %d (%s)\n", ret, errno, strerror(errno));

		while(1)
		{
			unsigned int clilen = sizeof(serv_addr);
			int newfd = accept(fd, (struct sockaddr *) &serv_addr, &clilen);

			char buf[256];
			int n = read(newfd, buf, 255);
			buf[n] = '\0';
			printf("received : %s\n", buf);
		}

		return ret;
	}
	
	int fd = socket(AF_INET, SOCK_STREAM, 0);
	if (fd < 0) 
		printf("ERROR opening socket\n");
	
	struct sockaddr_in serv_addr;

	memset(&serv_addr, 0, sizeof(serv_addr));
	
	int portno = 5555;
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
	serv_addr.sin_port = htons(portno);
	
	if ((ret = connect(fd, (struct sockaddr *) &serv_addr, sizeof(serv_addr))) < 0) 
	{
		printf("ERROR on connecting : %d, %d (%s)\n", ret, errno, strerror(errno));
		return ret;
	}
	
	dup2(fd, STDOUT_FILENO);
	ret = execl("./test.py", "test.py", "app-portage/kuroo4-4.2", "app-portage/kuroo4-4.3", NULL);
	printf("execl: (%d) %s\n", errno, strerror(errno));
	return ret;
}

void freeRunner(Runner *r)
{
	free(r);
}
