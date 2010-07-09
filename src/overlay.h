#ifndef OVERLAY_H
#define OVERLAY_H

typedef struct Overlay Overlay;

Overlay*	createOverlay(const char*, const char*, int, int);
const char*	overlayName(Overlay*);
const char*	overlayOwnerEmail(Overlay*);
int 		overlayPriority(Overlay*);
const char*	overlayDescription(Overlay*);
int 		overlayIsOfficial(Overlay*);
void		overlayFree(Overlay*);

#endif
