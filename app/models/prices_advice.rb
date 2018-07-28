class PricesAdvice < ApplicationRecord

  belongs_to :eve_item
  belongs_to :trade_hub
  belongs_to :region

  def self.get_results
    request = File.open( "#{Rails.root}/sql/select_prices_advices.sql" ).read
    connection.exec_query( request, :select_prices_advices, [ [ nil, false ], [ nil, 0,1 ] ] )
  end

end