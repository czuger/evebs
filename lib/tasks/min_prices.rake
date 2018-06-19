require 'open-uri'
# require 'open-uri/cached'
require 'pp'

# OpenURI::Cache.cache_path = 'tmp'

namespace :process do

  desc 'Download min prices'
  task :min_prices => :environment do
    # Esi::MinPrices.new(debug_request: true ).update( 10000042, 11689 )
    Esi::UpdatePricesMin.new(debug_request: false ).update()
  end

  desc 'Compute prices advices'
  task :prices_advices => :environment do
    PricesAdvice.update
  end

end