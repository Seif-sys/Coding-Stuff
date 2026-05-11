using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.RenderGraphModule.Util;

public class HomographyWarpFeature : ScriptableRendererFeature
{
    [System.Serializable]
    public class Settings { public Material material; } // "BlitWarp/HomographyWarp"
    public Settings settings = new Settings();

    class RGPass : ScriptableRenderPass
    {
        readonly Material mat;
        public RGPass(Material m) { mat = m; renderPassEvent = RenderPassEvent.AfterRendering; }

        public override void RecordRenderGraph(RenderGraph rg, ContextContainer frameData)
        {
            if (!mat) return;

            // Get active color texture (source for our warpping)
            var res  = frameData.Get<UniversalResourceData>();
            var src  = res.activeColorTexture;

            // Create a destination with same desc as active color
            var dstDesc = rg.GetTextureDesc(src);
            dstDesc.name = "_HomographyWarpDst";
            var dst = rg.CreateTexture(dstDesc);

            // Configure a blit pass (material pass 0)
            var blitParams = new RenderGraphUtils.BlitMaterialParameters(src, dst, mat, 0);
            rg.AddBlitPass(blitParams, "Homography Warp");

            // Make the warped texture the new camera color so we don't blit back
            res.cameraColor = dst;
        }
    }

    RGPass pass;
    public override void Create() => pass = new RGPass(settings.material);
    public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData rd) => renderer.EnqueuePass(pass);
}
