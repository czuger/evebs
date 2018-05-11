require 'open-uri'
require 'json'

class Esi::Download

  ESI_BASE_URL='https://esi.tech.ccp.is/latest/'
  ESI_DATA_SOURCE={ datasource: :tranquility }

  def initialize( rest_url, params = {}, debug_request: false )
    @debug_request = debug_request
    @rest_url = rest_url
    @params = params.merge( ESI_DATA_SOURCE )
  end

  def get_page( page_number=nil )
    @params[:page] = page_number if page_number
    url = build_url
    puts "Fetching : #{url}" if @debug_request

    begin
      @request = open( url )
      set_headers

      json_result = @request.read
      JSON.parse( json_result )
    rescue => e
      sleep 3
      return e
    end
  end

  def get_all_pages
    result = []
    @params[:page] = 1

    loop do
      puts "Requesting page #{@params[:page]}" if @debug_request

      pages = get_page

      unless pages.is_a? Array
        puts [ pages, @errors_limit_remain.to_s, @errors_limit_reset.to_s ].join( ', ' ) if @debug_request
        next
      end

      result += pages unless pages.empty?

      if @pages_count == 0 || @pages_count == 1
        break
      else
        puts "More pages to download : #{@pages_count}" if @debug_request
        @params[:page] += 1
      end

      if @params[:page] && @params[:page] > @pages_count
        @params.delete(:page)
        break
      end
    end

    result
  end

  private

  def set_headers
    @pages_count = @request.meta['x-pages'].to_i
    @errors_limit_remain = @request.meta['x-esi-error-limit-remain']
    @errors_limit_reset = @request.meta['x-esi-error-limit-reset']
  end

  def build_url
    url = ( @rest_url + '?' + @params.map{ |k, v| "#{k}=#{v}" }.join( '&' ) ).gsub( '//', '/' )
    ESI_BASE_URL + url
  end

  def load_headers
    open( @url ).meta
  end

end