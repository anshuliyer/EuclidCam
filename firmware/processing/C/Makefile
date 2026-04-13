CC = gcc
CFLAGS = -O3 -Wall -Wextra
LIBS = -lm

all: enhance

enhance: enhance.o cnn_inference.o
	$(CC) $(CFLAGS) -o enhance enhance.o cnn_inference.o $(LIBS)

enhance.o: enhance.c cnn_inference.h stb_image.h stb_image_write.h
	$(CC) $(CFLAGS) -c enhance.c

cnn_inference.o: cnn_inference.c cnn_inference.h
	$(CC) $(CFLAGS) -c cnn_inference.c

clean:
	rm -f *.o enhance
