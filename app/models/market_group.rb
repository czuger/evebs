class MarketGroup < ActiveRecord::Base

  has_many :eve_items
  acts_as_tree

  def get_market_group_breadcrumb
    prefix = ancestors.reverse.map{ |e| e.name }.join( ' > ' )
    prefix << ' > ' << name
  end

end
