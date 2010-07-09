#include "overlay.h"
#include "interpreter.h"

int main(int argc, char *argv[])
{
	interpreterInit();
	
	Overlay *o = createOverlay("<overlay type='svn' src='https://overlays.gentoo.org/svn/dev/wrobel' contact='nobody@gentoo.org' name='wrobel' status='official' priorit='10'><description>Test</description></overlay>", "", 1, 0);

	if (!o)
	{
		printf("Error creating overlay.\n");
		return 0;
	}
	
	printf("Overlay name = %s, owner email : %s, description : %s, priority : %d, it is %sofficial.\n", overlayName(o), overlayOwnerEmail(o), overlayDescription(o), overlayPriority(o), overlayIsOfficial(o) ? "" : "not ");

	interpreterFinalize();

	return 0;
}
