require_relative 'download'
require 'pp'

d = Download.new( 'markets/10000030/history/', { type_id: 12775 }, debug_request: true )
pp d.get_page

pp d