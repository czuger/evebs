class OrderAdvices
  def self.do
    costs = []
    systems =
      [ { id:30002510, name: 'Rens' },
        { id:30002053, name: 'Hek' } ]
    systems.each do |system|
      Shared::Cost.types_ids.each do |item_id|
        min_price = Orders::PriceWatcher.do( item_id, system[:id] )
        cost = Shared::Cost.full_hash_by_id( item_id )
        oa = Orders::OrderAdvice.new(
          min_price: min_price,
          type: cost[:name],
          system: system[:name],
          batch: cost[:batch_size])
        costs << oa
      end
    end
    costs.sort!
    costs.reject!{ |oa| oa.marge_pcent < 50 }
    current_orders = Orders::Orders.new.orders.map{ |e| [e.system,e.type_name] }
    # pp current_orders
    costs.reject!{ |oa| current_orders.include?( [oa.system,oa.type]) }
    # pp costs

    @rows = []
    costs.each do |oa|
      @rows << oa
    end

    # table = Terminal::Table.new :rows => rows, headings: [ 'System', 'Item', 'Gain', 'Marge brute (pour un batch)' ]
    # table.align_column 0, :left
    # table.align_column 1, :left
    # table.align_column 2, :right
    # table.align_column 3, :right
    @rows
  end
end