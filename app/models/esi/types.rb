class Esi::Types < Esi::Download

  def initialize( debug_request: false )
    super( 'universe/types', {}, debug_request: debug_request )
    # p @errors_limit_remain
  end

  def update
    p = get_all_pages
    pp p
  end



end