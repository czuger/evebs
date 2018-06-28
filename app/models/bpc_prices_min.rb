class BpcPricesMin < ApplicationRecord
  belongs_to :trade_hub
  belongs_to :blueprint_component

  def self.feed_table
    Banner.p 'About to update update_bpc_prices_mins'

    request = File.open( "#{Rails.root}/sql/update_bpc_prices_mins.sql" ).read
    ActiveRecord::Base.connection.execute( request )
  end

end
