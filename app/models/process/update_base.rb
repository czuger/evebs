module Process
  class UpdateBase

    def initialize( verbose_output: false )
      @verbose_output = verbose_output || (ENV['EBS_VERBOSE_OUTPUT'] == 'true')
    end

  end
end