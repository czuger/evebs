class MySellings
  def self.show
    api = EAAL::API.new( '3808229', 'BHgPtSRlWR3cMsSadewgfE8UAAf2jhvT4Vvdo5f4JMyLTemqOzPMVMtch4Ww9ZJj' )
    api.scope = 'char'
    api.WalletTransactions( characterID: '1866432960' ).transactions.each do |transaction|
      if transaction.transactionType == 'sell'
        type = transaction.typeName
        qtt = transaction.quantity
        price = transaction.price
        client = transaction.clientName
        station = transaction.stationName
        puts "#{type}, #{qtt}, #{price}, #{client}, #{station}, #{price.to_f*qtt.to_f}"
      end
    end
    nil
  end
end