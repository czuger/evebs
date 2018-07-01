class Sql::PricesMins

  def self.update
    ActiveRecord::Base.transaction do
      Banner.p 'About to update prices mins.'
      update_prices
      update_volumes
    end
  end

  private

  def self.update_prices
    request = File.open( "#{Rails.root}/sql/update_prices_mins.sql" ).read
    ActiveRecord::Base.connection.execute( request )
  end

  def self.update_volumes
    PricesMin.all.each do |pm|
      pm.volume = SalesOrder.where( trade_hub_id: pm.trade_hub_id, eve_item_id: pm.eve_item_id, price: pm.min_price ).sum( :volume )
      pm.save!
    end
  end

end