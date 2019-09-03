module Misc
	class BreadcrumbElement

		attr_reader :name, :url

		def initialize( name, url )
			@name = name
			@url = url
		end

	end
end