import re
import os
import sys
from optparse import OptionParser

def parseOptions():
	usage = "usage: %prog [options]"
	parser = OptionParser(usage=usage)
	parser.add_option("-d", "--download", action="store", dest="download", help="Download subtitles for specific media file.")
	parser.add_option("-r", "--rename", action="store", dest="path", help="Rename subtitles according to video files.")
	options, args = parser.parse_args()
	return options, args, parser

def downloadSubtitles(download):
	if download.endswith('.avi') or download.endswith('.mkv') or download.endswith('.mp4'):
		download = download[:-4]
	import xmlrpclib
	client = xmlrpclib.ServerProxy("http://api.opensubtitles.org/xml-rpc", allow_none=True)
	#for key, value in client.ServerInfo().iteritems():
	#	print "%s = %s" % (key, value)
	login = client.LogIn('','','eng',"OS Test User Agent")
	print login
	if login['status'] == '200 OK':
		query = {'query': 'south park', 
			 'season': 1, 'episode': 1, 
			 'sublanguageid': 'all',
		}
		search = client.SearchSubtitles(login['token'], [query])
		
		for i in search['data']:
			print i['SubDownloadLink']
		import urllib2
		response = urllib2.urlopen(search['data'][0]['SubDownloadLink'])
		output = open('test.gz','wb')
		output.write(response.read())
		output.close()
		#search = client.SearchSubtitles(login['token'], [{'sublanguageid': 'eng,cze,svk', 'query': download}])
		#print "Search is '%s'" % search
		#download = client.DownloadSubtitles(login['token'], [])

def renameSubtitles():
	if not os.path.exists(path):
		print 'Entered path "%s" is invalid!' % path
		sys.exit(-1)

	if not os.path.isdir(path):
		print 'Entered path "%s" is not a directory' % path
		sys.exit(-2)
	files = os.listdir(path)
	matched = 0
	renamed = 0
	print "Directory '%s' has %d files" % (path, len(files))

	sub_pattern = re.compile('.*(s|S)(?P<series>\d{1,2})(e|E)(?P<episode>\d{1,2}).*\.(srt|sub)$')

	for f in files:
		res = sub_pattern.match(f) 
		if res is not None:
			matched = matched + 1
			ep_pattern = re.compile('.*(s|S)%s(e|E)%s.*\.(avi|mkv|mp4)$' % ((res.group('series'), res.group('episode'))
	))
			#print 'Pattern matches %s' % f

			for ep_f in files:
				media_res = ep_pattern.match(ep_f)
				if media_res is not None:
					#print "Found media file: %s" % ep_f
					base_episode_file = ep_f.rsplit('.', 1)[0]
					subtitle_suffix = f.rsplit('.', 1)[-1]
					new_filename = base_episode_file + '.' + subtitle_suffix
					if f != new_filename:
						print '%s -> %s\n%s' % (f, new_filename, ep_f)
						os.rename(os.path.join(path, f), os.path.join(path, new_filename))
						renamed = renamed + 1
		else:
			pass#print 'Pattern does NOT match %s' % f
	print 'Renamed %d files' % renamed
	print 'Matched %d subtitle files' % matched

def main(options, args, parser):
	#print args, options
	if options.path and options.download:
		print "Cannot specify option -r and -d"
		sys.exit(-1)
	if options.path is None and options.download is None:
		print parser.print_help()
	if options.path is not None:
		renameSubtitles()
	elif options.download is not None:
		downloadSubtitles(options.download)

if __name__ == '__main__':
	options, args, parser = parseOptions()
	main(options, args, parser)
	sys.exit(0)
