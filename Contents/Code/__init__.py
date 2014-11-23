import urllib

EPISODES_URL = 'http://services.tvrage.com/myfeeds/episode_list.php?key=P8q4BaUCuRJPYWys3RBV&sid=%s'
SEARCH_URL = 'http://services.tvrage.com/myfeeds/search.php?key=P8q4BaUCuRJPYWys3RBV&show=%s'
SHOW_URL = 'http://services.tvrage.com/myfeeds/showinfo.php?key=P8q4BaUCuRJPYWys3RBV&sid=%s'

####################################################################################################
def Start():

	HTTP.CacheTime = CACHE_1DAY

####################################################################################################
class TVRageAgent(Agent.TV_Shows):

	name = 'TVRage'
	languages = [Locale.Language.English]
	primary_provider = True
	contributes_to = None

	def search(self, results, media, lang):

		search_results = XML.ElementFromURL(
			SEARCH_URL % urllib.quote(media.show),
			timeout=20,
		)
		show_id = search_results.xpath(("/Results/show/showid"
			"[preceding-sibling::name='{0}' or "
			"following-sibling::name='{0}']").format(media.show))
		start_year = search_results.xpath(("/Results/show/started"
			"[preceding-sibling::name='{0}' or "
			"following-sibling::name='{0}']").format(media.show))
		tvrage_id = str(show_id[0].text) if show_id else None
		year = int(start_year[0].text) if start_year else None

		if tvrage_id:
			results.Append(MetadataSearchResult(
				id=tvrage_id,
				name=media.show,
				score=100,
				year=year,
				lang=Locale.Language.English,
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

					title = episode_data[0].xpath('./title/text()')
					episode.title = title[0] if len(title) > 0 else None

					summary = episode_data[0].xpath('./summary/text()')
					episode.summary = summary[0] if len(summary) > 0 else None

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
