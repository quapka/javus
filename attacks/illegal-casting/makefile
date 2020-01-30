TARGET = illegalcasting
ANT = ant
# using aliases does not work straightforward within makefiles
GP = java -jar /home/qup/projects/fi/crocs/GlobalPlatformPro/gp.jar

all: $(TARGET)

$(TARGET):
	-rm $(TARGET).cap
	$(ANT) $@

reinstall: $(TARGET) install

install:
	$(GP) --force --install $(TARGET).cap --verbose --debug

uninstall:
	$(GP) --uninstall $(TARGET).cap --verbose --debug

apdu:
	$(GP) --apdu 00a404000b00112233445566778899aa --verbose --debug

deploy: $(TARGET) install apdu
