class SaleRecord < ActiveRecord::Base

  belongs_to :user
  belongs_to :eve_client
  belongs_to :station
  belongs_to :eve_item

  def self.get_sale_records

    # delete_all

    api = EAAL::API.new( '3808229', 'BHgPtSRlWR3cMsSadewgfE8UAAf2jhvT4Vvdo5f4JMyLTemqOzPMVMtch4Ww9ZJj' )
    api.scope = 'char'
    begin
      api.WalletTransactions( characterID: '1866432960' ).transactions.sort_by{ |e| e.transactionID }.each do |transaction|

        if transaction.transactionType == 'sell'

          # puts transaction.inspect
          # puts

          client = EveClient.get_client( transaction.clientID, transaction.clientName )

          item = EveItem.find_by_cpp_eve_item_id( transaction.typeID )
          puts "Can't find item #{transaction.typeID}, #{transaction.typeName}" unless item

          station = Station.find_by_cpp_station_id( transaction.stationID )
          puts "Can't find item #{transaction.stationID}, #{transaction.stationName}" unless station

          if item && station
            store_transaction( transaction, User.first, client, item, station )
          end

        end
      end
    rescue StandardError, EAAL::Exception => exception
      STDERR.puts Time.now
      STDERR.puts exception.message
      STDERR.puts exception.backtrace
    end
    nil
  end

  def self.store_transaction( transaction, user, client, item, station )

    transaction_key = transaction.transactionID.to_s + transaction.journalTransactionID.to_s

    created_transaction = where( eve_transaction_key: transaction_key ).first_or_create do |t|
      t.quantity = transaction.quantity.to_i
      t.unit_sale_price = transaction.price.to_f
      t.total_sale_price = t.quantity * t.unit_sale_price
      if item.cost
        blueprint = item.blueprint
        t.unit_cost = item.cost / blueprint.prod_qtt
        t.unit_sale_profit = t.unit_sale_price - t.unit_cost
        t.total_sale_profit = t.unit_sale_profit * t.quantity
      else
        puts "Could not compute profit for #{item.inspect}"
      end
      t.user_id = user.id
      t.eve_client_id = client.id
      t.eve_item_id = item.id
      t.station_id = station.id
      t.transaction_date_time = DateTime.parse( transaction.transactionDateTime )
    end
  end

end



