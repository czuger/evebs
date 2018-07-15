require 'open-uri'
require 'json'

class Esi::Download

  ESI_BASE_URL='https://esi.tech.ccp.is/latest/'
  ESI_DATA_SOURCE={ datasource: :tranquility }

  def initialize( rest_url, params = {}, debug_request: false )
    @debug_request = debug_request
    @rest_url = rest_url
    @params = params.merge( ESI_DATA_SOURCE )
    @forbidden_count = 0
  end

  def get_page( page_number=nil )
    @params[:page] = page_number if page_number
    url = build_url
    puts "Fetching : #{url}" if @debug_request

    begin
      @request = open( url )
    rescue => e
      Esi::Errors::Base.dispatch( e )
    end

    set_headers

    json_result = @request.read
    JSON.parse( json_result )
  end

  def get_page_retry_on_error( page_number=nil )
    loop do
      page = nil
      begin
        page = get_page
      rescue => e
        error_handling e
        next
      end
      return page
    end
  end

  def get_all_pages
    result = []
    @params[:page] = 1

    loop do
      puts "Requesting page #{@params[:page]}/#{@pages_count}" if @debug_request

      pages = nil
      begin
        pages = get_page
      rescue => e
        return false unless error_handling( e )
        next
      end

      unless pages.empty?
        result += pages if pages.is_a? Array
        result << pages if pages.is_a? Hash
      else
        puts "Page is empty" if @debug_request
      end

      if @pages_count == 0 || @pages_count == 1
        puts "No other pages to download - breaking out" if @debug_request
        break
      else
        puts "More pages to download : #{@pages_count}" if @debug_request
        @params[:page] += 1
      end

      if @params[:page] && @params[:page] > @pages_count
        puts "No more pages to download - breaking out" if @debug_request
        @params.delete(:page)
        break
      end
    end

    result
  end

  def set_auth_token( character=nil )
    unless character
      character_id = File.open( 'config/character_id.txt' ).read.to_i
      character = Character.find_by_eve_id( character_id )
    end

    if character.expires_on < Time.now().utc
      puts "Token expired - #{character.expires_on} < #{Time.now().utc}"
      renew_token( character )
    end

    @params[:token] = character.token
  end

  def renew_token( character )
    client_id = secret_key = nil
    if File.exists?( 'config/omniauth.yaml' )
      results = YAML.load( File.open( 'config/omniauth.yaml' ).read )

      if results && results[:esi]
        client_id, secret_key = results[:esi]
      end
    end

    auth64 = Base64.strict_encode64( "#{client_id}:#{secret_key}" )
    auth_string = "Basic #{auth64}"

    RestClient.log = 'stdout' if @debug_request

    c = RestClient.post 'https://login.eveonline.com/oauth/token',
                        { grant_type: :refresh_token, refresh_token: character.renew_token },
                        { 'Authorization' => auth_string }
    response = JSON.parse( c.body )

    character.update!( token: response['access_token'], expires_on: Time.now() + response['expires_in'] )
  end

  private

  def error_handling( e )
    puts "Requesting #{@rest_url}, #{@params.inspect} got #{e}, limit_remains = #{@errors_limit_remain}, limit_reset = #{@errors_limit_reset}"
    STDOUT.flush

    if e.is_a? Esi::Errors::Forbidden
      p @forbidden_count
      @forbidden_count += 1
      return false if @forbidden_count > 5
    elsif e.is_a? Esi::Errors::NotFound
      raise e
    elsif e.kind_of? Esi::Errors::Base
      e.pause
    else
      sleep 10
    end

    true
  end

  def set_headers
    @pages_count = @request.meta['x-pages'].to_i
    @errors_limit_remain = @request.meta['x-esi-error-limit-remain']
    @errors_limit_reset = @request.meta['x-esi-error-limit-reset']
  end

  def build_url
    url = ( @rest_url + '?' + @params.map{ |k, v| "#{k}=#{v}" }.join( '&' ) ).gsub( '//', '/' )
    ESI_BASE_URL + url
  end

end