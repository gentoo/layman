//#include "overlay.h"
#include "interpreter.h"
#include "config.h"
#include "laymanapi.h"
#include "message.h"

int main(int argc, char *argv[])
{
	argc = argc;
	argv = argv;
	int ret = 0;
	interpreterInit();
	
	Message *msg = messageCreate("layman", 0, 0, 0, 4, 2, 4, 4, 1, NULL, NULL, NULL);
	BareConfig *cfg = bareConfigCreate(msg, 0, 0, 0);
	if (!bareConfigSetOptionValue(cfg, "local_list", "/home/detlev/srg/gsoc2010/layman/layman/tests/testfiles/global-overlays.xml"))
		printf("Error setting config option.\n");
	//printf("config: %s\n", bareConfigGetDefaultValue(cfg, "config"));
	//printf("storage: %s\n", bareConfigGetDefaultValue(cfg, "storage"));
	//printf("local_list: %s\n", bareConfigGetDefaultValue(cfg, "local_list"));
	
	LaymanAPI *l = laymanAPICreate(cfg, 0, 0);
	if (!laymanAPIFetchRemoteList(l))
	{
		printf("Unable to fetch the remote list.\n");
		ret = -1;
		goto finish;
	}

	StringList *strs = laymanAPIGetAvailable(l);

	stringListPrint(strs);

finish:
	bareConfigFree(cfg);
	laymanAPIFree(l);

	interpreterFinalize();

	return ret;
}
