class MarketGroup < ApplicationRecord

  has_many :eve_items, dependent: :destroy
  serialize :cpp_type_ids
  acts_as_tree

  def breadcrumb( view_context )
		bc = [ Misc::BreadcrumbElement.new( 'Root', view_context.list_items_url ) ]
		bc += ancestors.reverse.map { |e| Misc::BreadcrumbElement.new( e.name, view_context.list_items_url( group_id: e.id ) ) }
		bc << Misc::BreadcrumbElement.new( name, view_context.list_items_url( group_id: id ) )
	end

end
