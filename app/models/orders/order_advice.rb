require 'constructor'

class Orders::OrderAdvice
  constructor :min_price, :type, :system, :batch, :accessors => true
  def marge_pcent
    ( ( @min_price * 100 ) / cost(@type) ).round(0) - 100
  end
  def marge_batch
    (( ( @min_price - cost(@type) ) * @batch )).round(2)
  end
  def <=>(pair)
    pair.marge_batch <=> marge_batch
  end
  private
  def cost(name)
    Shared::Cost.by_name(name)
  end
end