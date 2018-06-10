class PricesAdvice < ApplicationRecord

  belongs_to :eve_item
  belongs_to :trade_hub
  belongs_to :region

  def self.update
    Banner.p 'About to recompute prices advices.'

    request = File.open( "#{Rails.root}/sql/update_price_advices.sql" ).read
    ActiveRecord::Base.connection.execute( request )
  end

end