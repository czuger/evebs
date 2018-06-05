require_relative 'download'

class Esi::DownloadSellOrders < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: true )
  end

  def update

    character_id = Character.first.eve_id
    @rest_url = "/characters/#{character_id}/orders/"

    get_all_pages.each

  end

end