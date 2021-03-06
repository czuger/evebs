require 'open-uri'
require 'json'

class Esi::Download

  ESI_BASE_URL='https://esi.evetech.net/latest/'
  ESI_DATA_SOURCE={ datasource: :tranquility }

  def initialize( rest_url = nil, params = {}, debug_request: false, verbose_output: false )

    @debug_request = debug_request
    @verbose_output = verbose_output || (ENV['EBS_VERBOSE_OUTPUT'] == 'true')

    # p ENV['EBS_VERBOSE_OUTPUT']
    puts 'Esi::Download - verbosity on' if @verbose_output

    @rest_url = rest_url
    @params = params.merge( ESI_DATA_SOURCE )
    @forbidden_count = 0

  end

  def get_page( page_number=nil )
    @params[:page] = page_number if page_number
    url = build_url
    puts "Fetching : #{url}" if @debug_request

    parsed_result = nil

    loop do
      begin
        @request = open( url )

        set_headers

        json_result = @request.read
        parsed_result = JSON.parse( json_result )

        break

      rescue JSON::ParserError => parse_error
        warn 'Got parse error !!!'
        next

      rescue => e
        error = Esi::Errors::Base.dispatch( e )
        error_print( error )

        if error.retry?
          error.pause
          next

        else
          raise error
        end

      end
    end

    parsed_result
  end

  def get_page_retry_on_error( page_number=nil )
    get_page( page_number )
  end

  def get_all_pages( expect: nil )
    result = []
    @params[:page] = 1

    loop do
      puts "Requesting page #{@params[:page]}/#{@pages_count}" if @debug_request

      pages = get_page

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

  def set_auth_token( user=nil )

    # p user

    return false unless user.expires_on && user.token && user.renew_token

    unless user
      user_id = File.open( 'config/character_id.txt' ).read.to_i
      user = User.find_by_uid( user_id )
    end

    if user.expires_on < Time.now().utc
      puts "Token expired - #{user.expires_on} < #{Time.now().utc}"
      renew_token( user )
    end

    @params[:token] = user.token

    true
  end

  private

  def renew_token( user )
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
                        { grant_type: :refresh_token, refresh_token: user.renew_token },
                        { 'Authorization' => auth_string }
    response = JSON.parse( c.body )

    user.update!( token: response['access_token'], expires_on: Time.now() + response['expires_in'] )
  end

  def error_print( e )
    warn "#{Time.now} - Requesting #{@rest_url}, #{@params.inspect} got '#{e}', limit_remains = #{@errors_limit_remain}, limit_reset = #{@errors_limit_reset}"
    STDOUT.flush
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