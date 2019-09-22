module UsersHelper

  def trade_hub_from_hash_data( hash_data )
    "#{hash_data['trade_hubs.name']} (#{hash_data['regions.name']})"
  end

	# def render_haml(haml, locals = {}, &block)
	# 	Haml::Engine.new(haml.strip_heredoc, format: :html5).render(self, locals, &block)
	# end
	#
	# def bootstrap_field( f, field, text, &block )
	# 	render_haml <<-HAML, { field: field, text: text, f: f }, &block
	# 		.col-12.col-lg
	# 			.input-group
	# 				.input-group-prepend
	# 					%span.input-group-text
	# 						= t( '.' + field.to_s )
	# 						= help_tooltip field
	#
	# 				= yield
	# 	HAML
	# end

end