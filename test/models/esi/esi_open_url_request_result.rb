class EsiOpenUrlRequestResult

  def initialize( data, add_random_name_to_data: true )
    @data = data
    @add_random_name_to_data = add_random_name_to_data
  end

  def read
    @data[ 'name' ] = ( 'name test %f' % rand ) if @add_random_name_to_data
    return @data.to_json
  end

  def meta
    {}
  end

end