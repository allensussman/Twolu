from rottentomatoes import RT
import sys

def getPosterUrl(movieTitle):
	rt=RT()
	return rt.search(movieTitle)[0]['posters']['original']

def main():
	print getPosterUrl(sys.argv[1])

if __name__ == '__main__':
	main()