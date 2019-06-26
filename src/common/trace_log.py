from logging import getLogger, StreamHandler, DEBUG

class Trace_log():

	def get(self):
		logger = getLogger(__name__)
		handler = StreamHandler()
		handler.setLevel(DEBUG)
		logger.setLevel(DEBUG)
		logger.addHandler(handler)
		logger.propagate = False
		return logger


def main():
	trace_log = Trace_log()
	logger = trace_log.get()
	logger.debug('hello', exc_info=True, stack_info=True)

if __name__ == "__main__":
    main()
