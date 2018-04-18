class PricesAdvice < ApplicationRecord

  belongs_to :eve_item
  belongs_to :trade_hub
  belongs_to :region

  def self.update
    current_path = File.dirname( __FILE__ )
    request = File.open( "#{current_path}/sql/update_crest_price_advices.sql" ).read
    ActiveRecord::Base.connection.execute( request )
  end

end