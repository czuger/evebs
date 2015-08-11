class MySellings

  # TODO :
  # Create a SaleRecord entry
  # Create a link between SaleRecord and EveClient (see http://guides.rubyonrails.org/active_record_migrations.html#creating-a-join-table)
  # Add the link creatin into SaleRecord migration
  # In EveClient : create a method get_client_by_id wich create the client if he don't exist
  # Do the same for eve item
  # Have a look at station model, seems to fix the station issue.
  # Create all the link to station, eve_item as for SaleRecord and EveClient, see
  # Use transactionId + journalTransactionId as an uniq cpp_key use bigint as type for both (should work on postgres and sqlite)
  def self.show
    api = EAAL::API.new( '3808229', 'BHgPtSRlWR3cMsSadewgfE8UAAf2jhvT4Vvdo5f4JMyLTemqOzPMVMtch4Ww9ZJj' )
    api.scope = 'char'
    api.WalletTransactions( characterID: '1866432960' ).transactions.sort_by{ |e| e.transactionID }.each do |transaction|

      if transaction.transactionType == 'sell'
        type = transaction.typeName
        qtt = transaction.quantity
        price = transaction.price
        client = transaction.clientName
        station = transaction.stationName
        # puts "#{type}, #{qtt}, #{price}, #{client}, #{station}, #{price.to_f*qtt.to_f}"

        puts "#{transaction.transactionID}, #{transaction.journalTransactionID}"

      end
    end
    nil
  end

end