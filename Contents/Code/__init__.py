SHOW_URL = 'http://services.tvrage.com/myfeeds/showinfo.php?key=P8q4BaUCuRJPYWys3RBV&sid=%s'
EPISODES_URL = 'http://services.tvrage.com/myfeeds/episode_list.php?key=P8q4BaUCuRJPYWys3RBV&sid=%s'

####################################################################################################
def Start():

	HTTP.CacheTime = CACHE_1DAY

####################################################################################################
class TVRageAgent(Agent.TV_Shows):

	name = 'TVRage'
	languages = [Locale.Language.English]
	primary_provider = False
	contributes_to = [
		'com.plexapp.agents.themoviedb'
	]

	def search(self, results, media, lang):

		# Get the TVRage id from the Movie Database Agent
		tvrage_id = Core.messaging.call_external_function(
			'com.plexapp.agents.themoviedb',
			'MessageKit:GetTvRageId',
			kwargs = dict(
				tmdb_id = media.primary_metadata.id
			)
		)

		if tvrage_id:
			results.Append(MetadataSearchResult(
				id = tvrage_id,
				score = 100
			))
		else:
			Log(' *** Could not find TVRage id for "%s"' % media.primary_metadata.title)

	def update(self, metadata, media, lang):

		show_xml = XML.ElementFromURL(SHOW_URL % metadata.id)

		metadata.title = show_xml.xpath('/Showinfo/showname/text()')[0]
		metadata.summary = show_xml.xpath('/Showinfo/summary/text()')[0]

		episodes_xml = XML.ElementFromURL(EPISODES_URL % metadata.id)

		# Loop over seasons.
		for s in media.seasons:

			season = metadata.seasons[s]

			# Loop over episodes in a season.
			for e in media.seasons[s].episodes:

				episode = metadata.seasons[s].episodes[e]

				episode_data = episodes_xml.xpath('//Season[@no="%s"]/episode/seasonnum[text()="%s"]/..' % (s, e.zfill(2)))

				if len(episode_data) > 0:

					episode.title = episode_data[0].xpath('./title/text()')[0]
					episode.summary = episode_data[0].xpath('./summary/text()')[0]

					# Episode still.
					still = episode_data[0].xpath('./screencap/text()')
					valid_names = list()

					if len(still) > 0 and still[0] != '':

						valid_names.append(still[0])

						if still[0] not in episode.thumbs:
							try:
								episode.thumbs[still[0]] = Proxy.Media(HTTP.Request(still[0]).content)
							except:
								pass

					episode.thumbs.validate_keys(valid_names)
