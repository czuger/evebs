require 'test_helper'

class EsiRequestResult

  def initialize( data )
    @data = data
  end

  def read
    @data[ 'name' ] = ( "name test %f" % rand )
    return @data.to_json
  end

  def meta
    {}
  end

end

class DownloadBlueprintsTest < ActiveSupport::TestCase

  def setup
    blueprint_type = EsiRequestResult.new(
        { 'published': true, 'blueprintTypeID': 1, 'quantity': 5, 'typeID': 10, 'volume': 5 } )

    @ub = Esi::UpdateBlueprints.new
    @ub.stubs( :open ).with(regexp_matches( /.*\/universe\/types\/.*/ )).returns( blueprint_type )

    YAML.stubs( :load_file ).returns [ {
        1 => { 'activities' => {
            'manufacturing' => {
                'materials' => [ { 'typeID' => 500, 'quantity' => 500 } ],
                'products' => [ { 'quantity' => 10, 'typeID' => 30 } ] } },
               'maxProductionLimit' => 50,
            'blueprintTypeID' => 1}
                                       } ]
  end

  test 'update blueprints' do
    @ub.update
  end

end