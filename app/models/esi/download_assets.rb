module Esi
  class DownloadAssets < Download

    def get_list

      Banner.p 'About to download assets'

      set_auth_token

      @rest_url = "characters/#{@character.eve_id}/assets/"
      get_all_pages
    end

  end
end
