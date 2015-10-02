class MarketGroup < ActiveRecord::Base

  has_many :eve_items
  acts_as_tree

  OVERCLASSIFICATION = %w( Large Medium Small )

  def get_market_group_breadcrumb
    prefix = ancestors.reverse.map{ |e| e.name }.compact.join( ' > ' )
    prefix << ' > ' << name unless OVERCLASSIFICATION.include?( name )
    prefix
  end

end
