def number_decorator(func):
	def wrapper(*args):
		args_array = [*args]

		if len(args_array) == 0:
			return func() 

		return args_array[0](func())

	return wrapper


@number_decorator
def zero():
	return 0


def main():
	print(zero(lambda x: x + 5))

if __name__ == '__main__':
	main()