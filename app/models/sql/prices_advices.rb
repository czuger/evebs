class Sql::PricesAdvices

  def self.update
    ActiveRecord::Base.transaction do
      Banner.p 'About to update prices advices'

      request = File.open( "#{Rails.root}/sql/update_prices_advices.sql" ).read
      ActiveRecord::Base.connection.execute( request )
    end
  end

end