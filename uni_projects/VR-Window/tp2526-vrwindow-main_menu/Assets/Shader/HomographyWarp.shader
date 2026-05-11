Shader "BlitWarp/HomographyWarp"
{
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" }
        ZTest Always ZWrite Off Cull Off

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            // Blitter binds these names:
            TEXTURE2D(_BlitTexture);
            float4 _BlitScaleBias;      // xy = scale, zw = bias (set by Blitter)

            // float3x3 _HInv;             // inverse homography: destUV -> srcUV, both in [0,1]
            float4x4 _HInv;             // inverse homography: destUV -> srcUV, both in [0,1]

            struct VOut { float4 pos:SV_Position; float2 uv:TEXCOORD0; };

            VOut vert(uint id:SV_VertexID)
            {
                // full-screen triangle
                float2 v = float2(id==2 ? 2.0 : 0.0, id==1 ? 2.0 : 0.0);
                VOut o = {float4(v*2.0-1.0, 0, 1), v};
                
                return o;
            }

            half4 frag(VOut i) : SV_Target
            {
                // Normalize FS-triangle coords using Blitter’s scale+bias
                float2 dstUV = i.uv * _BlitScaleBias.xy + _BlitScaleBias.zw; // 0..1
                // // flip Y on Windows, because WHY THE FUCK is the blit target upside down there???
                dstUV.y = 1.0 - dstUV.y;


                // Projective lookup via H^{-1}
                // float3 uvw = mul(_HInv, float3(dstUV, 1.0));
                float3 uvw = mul(_HInv, float4(dstUV, 1.0, 1.0)).xyz;
                float2 srcUV = uvw.xy / uvw.z;

                if (srcUV.x < 0 || srcUV.x > 1 || srcUV.y < 0 || srcUV.y > 1) return 0;

                return SAMPLE_TEXTURE2D(_BlitTexture, sampler_LinearClamp, srcUV);
            }
            ENDHLSL
        }
    }
}
